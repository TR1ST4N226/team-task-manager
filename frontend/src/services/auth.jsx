import api from './api'

export const login = (email, password) => {
  return api.post('/auth/login', { email, password })
    .then(res => res.data)
}

export const register = (userData) => {
  return api.post('/auth/register', userData)
    .then(res => res.data)
}

export const getProfile = () => {
  return api.get('/auth/me')
    .then(res => res.data)
}

export const changePassword = (oldPassword, newPassword) => {
  return api.post('/auth/change-password', { old_password: oldPassword, new_password: newPassword })
    .then(res => res.data)
}