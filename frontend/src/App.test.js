import { render, screen } from '@testing-library/react';
import App from './App';

test('renders surveillance dashboard title', () => {
  render(<App />);
  // This looks for your new project title instead of the old React link
  const titleElement = screen.getByText(/COMMAND CENTER: BORDER SURVEILLANCE/i);
  expect(titleElement).toBeInTheDocument();
});