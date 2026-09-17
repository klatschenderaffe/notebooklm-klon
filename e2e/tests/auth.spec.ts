import { expect, test } from '@playwright/test'

// Diese Tests laufen bewusst ohne echte Supabase/Gemini-Credentials -- es wird nur
// geprüft, was rein clientseitig passiert (Formularfelder, Redirects), ohne dass ein
// echter Login stattfindet.

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
