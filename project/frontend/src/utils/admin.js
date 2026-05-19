export function isAdmin() {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  return user?.role === 'admin'
}
