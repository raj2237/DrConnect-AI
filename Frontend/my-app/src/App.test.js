import { render, screen } from '@testing-library/react';
import App from './App';

test('renders DrConnect brand in header', () => {
  render(<App />);
  const brand = screen.getByText(/DrConnect/i);
  expect(brand).toBeInTheDocument();
});
