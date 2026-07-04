import { Link, useLocation } from 'react-router-dom';
import './NavBar.css';

export default function NavBar() {
  const location = useLocation();

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span className="navbar-brand-mark">MHR</span>
      </Link>
      <Link
        to="/history"
        className={`navbar-link ${location.pathname === '/history' ? 'active' : ''}`}
      >
        Patient History
      </Link>
    </nav>
  );
}