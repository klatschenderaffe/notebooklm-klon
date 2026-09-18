import AppHeader from '../components/AppHeader'

function ImpressumPage() {
  return (
    <>
      <AppHeader />
      <main className="app-main">
        <div className="legal-page">
          <p className="legal-warning">
            ⚠️ <strong>Muster-Impressum.</strong> Die mit <code>[…]</code> markierten Angaben sind
            Platzhalter und müssen durch echte, vollständige Angaben ersetzt werden, bevor diese
            Seite mit echten Nutzer:innen live betrieben wird. Ein unvollständiges oder falsches
            Impressum ist selbst ein häufiger Abmahngrund.
          </p>

          <h2>Impressum</h2>
          <p>Angaben gemäß § 5 TMG</p>

          <h3>Anbieter</h3>
          <p>
            [Vollständiger Name]
            <br />
            [Straße und Hausnummer]
            <br />
            [PLZ und Ort]
          </p>

          <h3>Kontakt</h3>
          <p>
            E-Mail: [E-Mail-Adresse]
            <br />
            Telefon: [Telefonnummer] (optional)
          </p>

          <h3>Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV</h3>
          <p>[Vollständiger Name, wie oben]</p>

          <h3>Streitschlichtung</h3>
          <p>
            Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS)
            bereit: <a href="https://ec.europa.eu/consumers/odr/">https://ec.europa.eu/consumers/odr/</a>.
            Wir sind nicht verpflichtet und nicht bereit, an Streitbeilegungsverfahren vor einer
            Verbraucherschlichtungsstelle teilzunehmen. [Bitte prüfen und ggf. anpassen, falls
            zutreffend.]
          </p>
        </div>
      </main>
    </>
  )
}

export default ImpressumPage
