// Asks the backend whether it and the database are healthy.
// Components never call the server by themselves; they use this file.

export async function getHealth() {
  const response = await fetch('/api/v1/health')

  if (!response.ok) {
    throw new Error(`The API answered ${response.status}`)
  }

  return response.json()
}
