import AppHeader from '../components/AppHeader'

function DatenschutzPage() {
  return (
    <>
      <AppHeader />
      <main className="app-main">
        <div className="legal-page">
          <p className="legal-warning">
            ⚠️ <strong>Entwurf/Vorlage, keine Rechtsberatung.</strong> Dieser Text beschreibt
            wahrheitsgemäß, welche Dienste diese App technisch einsetzt und welche Daten dabei
            anfallen. Er ersetzt keine rechtliche Prüfung — vor dem echten Betrieb mit echten
            Nutzer:innen sollte das von einer fachkundigen Stelle gegengelesen werden. Die
            Betreiber-Angaben (Platzhalter <code>[…]</code>) sind identisch mit dem{' '}
            <a href="/impressum">Impressum</a> auszufüllen.
          </p>

          <h2>Datenschutzerklärung</h2>

          <h3>1. Verantwortlicher</h3>
          <p>
            [Vollständiger Name]
            <br />
            [Straße und Hausnummer], [PLZ und Ort]
            <br />
            E-Mail: [E-Mail-Adresse]
          </p>

          <h3>2. Was diese App macht</h3>
          <p>
            NotebookLM-Klon ermöglicht es angemeldeten Nutzer:innen, eigene Quellen (PDF, Markdown,
            Webseiten) in "Notebooks" zu sammeln, dazu per Chat Fragen zu stellen und
            Präsentationen erstellen zu lassen. Dafür ist zwingend ein Nutzerkonto erforderlich.
          </p>

          <h3>3. Registrierung und Anmeldung</h3>
          <p>
            Für die Kontoerstellung verarbeiten wir E-Mail-Adresse und Passwort. Das Passwort wird
            nicht im Klartext gespeichert. Anmeldung und Sitzungsverwaltung laufen über{' '}
            <strong>Supabase Auth</strong> (Supabase, Inc.); die Sitzung wird als Zugriffs-Token im
            lokalen Speicher (<code>localStorage</code>) deines Browsers abgelegt, nicht als
            klassisches Cookie. Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO (Vertragserfüllung –
            Bereitstellung des Nutzerkontos).
          </p>

          <h3>4. Von dir hochgeladene Inhalte</h3>
          <p>
            Alle Inhalte, die du in einem Notebook anlegst — hochgeladene Dateien, eingegebene
            URLs, daraus extrahierter Text, deine Chat-Fragen und die generierten
            Antworten samt Zitaten, eigene Notizen sowie erzeugte Präsentationen — werden in
            unserer Datenbank und unserem Datei-Speicher bei <strong>Supabase</strong> gespeichert,
            ausschließlich sichtbar für dein eigenes Konto (technisch u.a. über
            Row-Level-Security abgesichert). Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO.
          </p>

          <h3>5. KI-gestützte Verarbeitung (Google Gemini API)</h3>
          <p>
            Um Fragen zu beantworten, Texte zu verarbeiten (Embeddings) und Präsentationen zu
            erzeugen, werden die relevanten Inhalte deiner Quellen sowie deine Chat-Eingaben an die{' '}
            <strong>Google Gemini API</strong> (Google Ireland Limited bzw. Google LLC) übermittelt
            und dort verarbeitet. Das kann eine Übermittlung in ein Drittland (USA) einschließen;
            Google verweist hierfür auf Standardvertragsklauseln bzw. das EU-US Data Privacy
            Framework als Schutzmaßnahme. Rechtsgrundlage: Art. 6 Abs. 1 lit. b DSGVO
            (Vertragserfüllung), da diese Verarbeitung die Kernfunktion der App darstellt.
          </p>

          <h3>6. Hosting und technische Infrastruktur</h3>
          <ul>
            <li>
              <strong>Supabase</strong> (Datenbank, Authentifizierung, Datei-Speicher) —
              verarbeitet Konto- und Inhaltsdaten wie oben beschrieben.
            </li>
            <li>
              <strong>Render</strong> (Backend-Hosting, USA) — verarbeitet technische
              Zugriffsdaten (u.a. IP-Adresse, Zeitpunkt) beim Aufruf der Server-Schnittstelle, wie
              bei jedem Webserver-Betrieb technisch notwendig.
            </li>
            <li>
              <strong>Cloudflare</strong> (Auslieferung des Frontends, CDN, USA) — verarbeitet
              ebenfalls technische Zugriffsdaten (IP-Adresse, Browser-Kennung) zur Auslieferung und
              zum Schutz vor Missbrauch.
            </li>
          </ul>

          <h3>7. Fehler- und Performance-Monitoring (Sentry)</h3>
          <p>
            Tritt ein technischer Fehler auf, wird ein Fehlerbericht an <strong>Sentry</strong>{' '}
            übermittelt, verarbeitet über ein Rechenzentrum in Frankfurt (EU). Fehlerberichte
            enthalten bewusst nur deine interne Nutzer-ID, nicht deine E-Mail-Adresse, IP-Adresse
            oder sonstige Kontaktdaten. Ein Teil der Anfragen wird zusätzlich zur
            Performance-Messung (Ladezeiten, Serverantwortzeiten) erfasst. Rechtsgrundlage: Art. 6
            Abs. 1 lit. f DSGVO (berechtigtes Interesse an einem funktionierenden, fehlerfreien
            Betrieb).
          </p>

          <h3>8. Verfügbarkeitsüberwachung (UptimeRobot)</h3>
          <p>
            Ein externer Dienst (UptimeRobot) prüft in regelmäßigen Abständen automatisiert, ob
            unsere Server erreichbar sind. Dabei werden keine personenbezogenen Daten von
            Besucher:innen der App verarbeitet, nur die technische Erreichbarkeit eines
            öffentlichen Status-Endpunkts.
          </p>

          <h3>9. Cookies und lokaler Speicher</h3>
          <p>
            Wir setzen keine Marketing- oder Tracking-Cookies ein. Im Browser-Speicher
            (<code>localStorage</code>) werden ausschließlich technisch notwendige Daten abgelegt:
            dein Anmelde-Token und deine Theme-Einstellung (hell/dunkel). Eine Einwilligung nach §
            25 TTDSG ist dafür nicht erforderlich, da es sich um technisch notwendige Funktionen
            handelt, die du selbst aktiv nutzt.
          </p>

          <h3>10. Speicherdauer</h3>
          <p>
            Deine Daten werden gespeichert, solange dein Konto besteht. Auf Anfrage an [E-Mail-Adresse]
            werden dein Konto und alle zugehörigen Inhalte gelöscht.
          </p>

          <h3>11. Deine Rechte</h3>
          <p>Du hast nach der DSGVO das Recht auf:</p>
          <ul>
            <li>Auskunft über die zu dir gespeicherten Daten (Art. 15 DSGVO)</li>
            <li>Berichtigung unrichtiger Daten (Art. 16 DSGVO)</li>
            <li>Löschung deiner Daten (Art. 17 DSGVO)</li>
            <li>Einschränkung der Verarbeitung (Art. 18 DSGVO)</li>
            <li>Datenübertragbarkeit (Art. 20 DSGVO)</li>
            <li>Widerspruch gegen die Verarbeitung (Art. 21 DSGVO)</li>
          </ul>
          <p>
            Zudem hast du das Recht, dich bei einer Datenschutz-Aufsichtsbehörde zu beschweren.
          </p>

          <h3>12. Änderungen dieser Erklärung</h3>
          <p>
            Wir passen diese Datenschutzerklärung an, wenn sich die App oder die eingesetzten
            Dienste ändern. Es gilt jeweils die zum Zeitpunkt deines Besuchs aktuelle Fassung.
          </p>
        </div>
      </main>
    </>
  )
}

export default DatenschutzPage
