import { Link } from 'react-router-dom'

function AppFooter() {
  return (
    <footer className="app-footer">
      <Link to="/impressum">Impressum</Link>
      <Link to="/datenschutz">Datenschutz</Link>
    </footer>
  )
}

export default AppFooter
