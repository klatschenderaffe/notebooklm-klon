import { expect, test } from '@playwright/test'

// Die Tests unten (Formularfelder, unauthentifizierte Redirects) laufen bewusst ohne
// echte Supabase-Credentials -- es wird nur geprüft, was rein clientseitig passiert,
// ohne dass ein echter Login stattfindet. Der Test in "Echte Staging-Verbindung" weiter
// unten ist die Ausnahme: der führt absichtlich einen echten Login gegen die Staging-
// Umgebung durch, um die komplette Kette (Frontend + Backend + DB) zu verifizieren.

test.describe('Login-Seite', () => {
  test('rendert die erwarteten Formularfelder', async ({ page }) => {
    await page.goto('/login')

    await expect(page.getByRole('heading', { name: 'Anmelden' })).toBeVisible()
    await expect(page.getByPlaceholder('E-Mail')).toBeVisible()
    await expect(page.getByPlaceholder('Passwort')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Anmelden' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Registrieren' })).toBeVisible()
  })
})

test.describe('Signup-Seite', () => {
  test('rendert die erwarteten Formularfelder', async ({ page }) => {
    await page.goto('/signup')

    await expect(page.getByRole('heading', { name: 'Konto erstellen' })).toBeVisible()
    await expect(page.getByPlaceholder('E-Mail')).toBeVisible()
    await expect(page.getByPlaceholder('Passwort (mind. 6 Zeichen)')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Registrieren' })).toBeVisible()
    await expect(page.getByRole('link', { name: 'Anmelden' })).toBeVisible()
  })
})

test.describe('Geschützte Routen', () => {
  test('unauthentifizierter Zugriff auf /dashboard redirected zu /login', async ({ page }) => {
    await page.goto('/dashboard')

    await expect(page).toHaveURL(/\/login$/)
    await expect(page.getByRole('heading', { name: 'Anmelden' })).toBeVisible()
  })

  test('unauthentifizierter Zugriff auf / redirected zu /login', async ({ page }) => {
    await page.goto('/')

    await expect(page).toHaveURL(/\/login$/)
  })
})

// Tag '@staging' wird in playwright.config.ts benutzt, um dieser Test-Gruppe --
// und NUR dieser Gruppe -- über ein eigenes Projekt mit trace: 'off' zu geben.
// (test.use({ trace }) direkt in einer describe-Gruppe ist von Playwright nicht
// erlaubt, da das einen neuen Worker erzwingen würde: "Cannot use({ trace }) in
// a describe group". Projekt-basiertes Tagging ist der von Playwright
// vorgesehene Weg dafür.)
test.describe('Echte Staging-Verbindung', { tag: '@staging' }, () => {
  // Dieser Test führt einen echten Login über Supabase gegen die Staging-Umgebung
  // durch und prüft danach, dass das Dashboard den eingeloggten Nutzer anzeigt.
  // Das soll zwei Dinge gleichzeitig beweisen: der Login-Flow gegen das echte
  // Supabase-Staging-Projekt funktioniert, UND der anschließende GET /notebooks-
  // Call ans echte Render-Staging-Backend funktioniert.
  //
  // Wichtig: die "Willkommen"-Überschrift in DashboardPage.tsx wird synchron
  // gerendert und hängt NICHT vom Ausgang des listNotebooks()-Calls ab (der läuft
  // als Fire-and-Forget in einem useEffect). Ein alleiniges Warten auf die
  // Überschrift würde also auch dann grün durchlaufen, wenn das Render-Backend
  // komplett offline wäre. Deshalb wird hier zusätzlich explizit auf die Network-
  // Response des GET /notebooks-Requests gewartet und deren Status geprüft --
  // nur so testet dieser Test wirklich die komplette Kette (Frontend + Supabase +
  // Backend), so wie es der Name verspricht.
  //
  // Tracing ist für diese Test-Gruppe bewusst deaktiviert (siehe das '@staging'-
  // Projekt in playwright.config.ts): der Test tippt ein echtes Staging-Passwort
  // per .fill() ein, und ein Trace mit Klartext-Passwort darf in einem Artifact
  // eines öffentlichen Repos nicht entstehen können -- unabhängig davon, welcher
  // Reporter/welche Artifact-Konfiguration gerade aktiv ist.
  //
  // Ohne gesetzte Zugangsdaten (z.B. bei einem lokalen Testlauf ohne Secrets)
  // wird der Test übersprungen statt fehlzuschlagen.

  const testEmail = process.env.E2E_TEST_USER_EMAIL
  const testPassword = process.env.E2E_TEST_USER_PASSWORD

  test('Login mit echten Zugangsdaten führt zum Dashboard mit erfolgreichem Notebooks-Call', async ({
    page,
  }) => {
    test.skip(
      !testEmail || !testPassword,
      'E2E_TEST_USER_EMAIL/E2E_TEST_USER_PASSWORD nicht gesetzt -- überspringe echten Login-Test.'
    )

    // Render-Free-Tier-Instanzen können nach Inaktivität langsam aufwachen (Cold
    // Start von bis zu ~50s ist auf dem Free Tier üblich). Der Login gegen
    // Supabase selbst ist davon nicht betroffen und läuft schnell -- die
    // Zeitbudgets unten sind entsprechend verteilt, damit ihre Summe unter
    // diesem äußeren Test-Timeout bleibt.
    test.setTimeout(90000)

    // Muss VOR dem Login-Klick aufgesetzt werden, da der GET /notebooks-Request
    // unmittelbar nach dem Redirect aufs Dashboard feuert (fire-and-forget in
    // einem useEffect) -- ein erst danach registrierter Listener könnte ihn
    // verpassen.
    const notebooksResponsePromise = page.waitForResponse(
      (response) => /\/notebooks$/.test(response.url()) && response.request().method() === 'GET',
      { timeout: 60000 }
    )

    await page.goto('/login')

    await page.getByPlaceholder('E-Mail').fill(testEmail as string)
    await page.getByPlaceholder('Passwort').fill(testPassword as string)
    await page.getByRole('button', { name: 'Anmelden' }).click()

    await expect(page).toHaveURL(/\/dashboard$/, { timeout: 10000 })
    await expect(page.getByRole('heading', { name: `Willkommen, ${testEmail}` })).toBeVisible({
      timeout: 10000,
    })

    // Die eigentliche Verifikation der kompletten Kette: der GET /notebooks-Call
    // ans Render-Backend muss wirklich mit 200 beantwortet worden sein. Schlägt
    // das Backend fehl oder antwortet mit einem Fehlerstatus, schlägt dieser Test
    // jetzt fehl -- unabhängig davon, was im DOM sichtbar ist.
    const notebooksResponse = await notebooksResponsePromise
    expect(notebooksResponse.status()).toBe(200)

    // Zusätzliche Absicherung: bei einem fehlgeschlagenen Call würde DashboardPage
    // zusätzlich eine Fehlermeldung rendern.
    await expect(page.locator('.error-text')).toHaveCount(0)
  })
})
