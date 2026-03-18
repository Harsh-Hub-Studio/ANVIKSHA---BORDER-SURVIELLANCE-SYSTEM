const fs = require('fs');
const path = require('path');
const cv = require('opencv4nodejs'); // JS equivalent of cv2
const yargs = require('yargs/yargs'); // JS equivalent of argparse
const { hideBin } = require('yargs/helpers');

// Assuming you have equivalent JS modules for these
const settings = require('./config/settings');
const { ObjectDetector, BehaviorAnalyzer, FenceTamperingDetector, BorderCrossingDetector } = require('./src/detection');
const Visualizer = require('./src/visualization');
const { logger, SurveillanceLogger } = require('./utils/logger');
const alertManager = require('./utils/alerting');

class SurveillanceSystem {
    constructor(videoSource = null, outputPath = null, showDisplay = true) {
        // Create output directory if needed
        this.outputDir = path.join(__dirname, '..', 'output');
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }

        // Create snapshots directory
        this.snapshotsDir = path.join(this.outputDir, 'snapshots');
        if (!fs.existsSync(this.snapshotsDir)) {
            fs.mkdirSync(this.snapshotsDir, { recursive: true });
        }

        // Initialize video source
        this.videoSource = videoSource !== null ? videoSource : settings.VIDEO_SOURCE;
        this.cap = this._initVideoCapture(this.videoSource);

        // Initialize video writer if output path provided
        this.outputPath = outputPath;
        this.writer = null;

        // Initialize detection and analysis components
        this.objectDetector = new ObjectDetector();
        this.behaviorAnalyzer = new BehaviorAnalyzer();
        this.fenceTamperingDetector = new FenceTamperingDetector();
        this.borderCrossingDetector = new BorderCrossingDetector();
        this.visualizer = new Visualizer();

        // Set up display option
        this.showDisplay = showDisplay;

        // Initialize logging
        this.loggerInstance = new SurveillanceLogger();

        // Initialize system state
        this.running = false;
        this.frameCount = 0;
        this.lastSnapshotTime = 0;

        logger.info("Surveillance system initialized successfully");
    }

    _initVideoCapture(source) {
        let cap;
        // Check if source is a number (camera index) or a string (file path)
        if (!isNaN(source)) {
            cap = new cv.VideoCapture(parseInt(source));
        } else {
            cap = new cv.VideoCapture(source);
        }

        // Set resolution (Note: syntax varies slightly in opencv4nodejs)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, settings.FRAME_WIDTH);
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, settings.FRAME_HEIGHT);
        cap.set(cv.CAP_PROP_FPS, settings.FPS);

        return cap;
    }

    _initVideoWriter(frameSize) {
        if (this.outputPath) {
            const fourcc = cv.VideoWriter.fourcc('XVID');
            const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 15);
            
            let outputFile = this.outputPath;
            if (fs.statSync(this.outputPath).isDirectory()) {
                outputFile = path.join(this.outputPath, `surveillance_${timestamp}.avi`);
            }

            this.writer = new cv.VideoWriter(outputFile, fourcc, settings.FPS, frameSize);
            logger.info(`Recording video to: ${outputFile}`);
        }
    }

    _saveSnapshot(frame, alert) {
        const currentTime = Date.now() / 1000;

        // Rate limit snapshots (max 1 per second)
        if (currentTime - this.lastSnapshotTime < 1.0) {
            return null;
        }

        // Create annotated snapshot
        const snapshot = this.visualizer.createSnapshot(frame, alert);

        // Save to file with timestamp
        const timestamp = new Date().toISOString().replace(/[-:T]/g, '').slice(0, 15);
        const alertType = alert.type.replace(/ /g, '_');
        const filename = `${alertType}_${timestamp}.jpg`;
        const filepath = path.join(this.snapshotsDir, filename);

        cv.imwrite(filepath, snapshot);
        logger.info(`Saved alert snapshot to ${filepath}`);

        // Update snapshot timestamp
        this.lastSnapshotTime = currentTime;

        return filepath;
    }

    async run() {
        this.running = true;
        logger.info("Starting surveillance system");

        if (this.outputPath) {
            // Pass size from first frame or settings
            this._initVideoWriter(new cv.Size(settings.FRAME_WIDTH, settings.FRAME_HEIGHT));
        }

        // Using a recursive async loop so we don't block the Node event loop
        const processNextFrame = async () => {
            if (!this.running) return;

            try {
                let frame = this.cap.read();
                if (frame.empty) {
                    logger.info("End of video stream");
                    this.stop();
                    return;
                }

                // Resize frame
                frame = frame.resize(settings.FRAME_HEIGHT, settings.FRAME_WIDTH);
                this.frameCount++;

                // Object detection
                const detections = await this.objectDetector.detect(frame);

                // Analysis
                const behaviorAlerts = await this.behaviorAnalyzer.update(detections, frame);
                const tamperingAlerts = await this.fenceTamperingDetector.detect(frame);
                const borderCrossingAlerts = await this.borderCrossingDetector.detect(detections, frame);

                const allAlerts = [...behaviorAlerts, ...tamperingAlerts, ...borderCrossingAlerts];

                // Process alerts
                if (allAlerts.length > 0) {
                    for (const alert of allAlerts) {
                        const snapshotPath = this._saveSnapshot(frame, alert);
                        let location = null;
                        if (settings.GPS_ENABLED) {
                            location = [settings.DEFAULT_LAT, settings.DEFAULT_LON];
                        }
                        
                        alertManager.sendAlert({
                            alertType: alert.type,
                            message: alert.message,
                            location: location,
                            imagePath: snapshotPath,
                            confidence: alert.confidence || 0.0
                        });
                        
                        this.loggerInstance.logAlert(alert.type, alert.message);
                    }
                }

                // Visualize results
                let processedFrame = frame.copy();
                processedFrame = this.visualizer.drawDetections(processedFrame, detections);
                processedFrame = this.visualizer.drawAlerts(processedFrame, allAlerts);
                processedFrame = this.visualizer.drawFenceRegions(processedFrame, settings.FENCE_REGIONS);
                processedFrame = this.visualizer.drawBorderLines(processedFrame, settings.BORDER_LINES);
                processedFrame = this.visualizer.addInfoOverlay(processedFrame, detections.length);

                // Display
                if (this.showDisplay) {
                    cv.imshow("Border Surveillance", processedFrame);
                    const key = cv.waitKey(1);
                    if (key === 113) { // 'q' key
                        logger.info("User requested exit");
                        this.stop();
                        return;
                    }
                }

                if (this.writer) {
                    this.writer.write(processedFrame);
                }

                // Schedule next frame
                setImmediate(processNextFrame);

            } catch (error) {
                logger.error(`Error in surveillance system: ${error.message}`);
                this.stop();
            }
        };

        // Start the loop
        processNextFrame();
    }

    stop() {
        this.running = false;
        this.cap.release();
        if (this.writer) {
            this.writer.release();
        }
        cv.destroyAllWindows();
        logger.info("Surveillance system stopped");
    }
}

// CLI Parsing
const argv = yargs(hideBin(process.argv))
    .option('source', {
        alias: 's',
        description: 'Video source (camera index or file path)',
        default: settings.VIDEO_SOURCE || 0,
        type: 'string'
    })
    .option('output', {
        alias: 'o',
        description: 'Output video file or directory',
        default: null,
        type: 'string'
    })
    .option('no-display', {
        description: 'Disable the video display window',
        type: 'boolean'
    })
    .help()
    .alias('help', 'h')
    .argv;

const system = new SurveillanceSystem(
    argv.source,
    argv.output,
    !argv['no-display']
);

system.run();