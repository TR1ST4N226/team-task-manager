import React, { createContext, useState, useContext, useEffect } from 'react'
import { login as apiLogin, register as apiRegister, getProfile } from '../services/auth'
import toast from 'react-hot-toast'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(() => localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      loadUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const loadUser = async () => {
    try {
      const response = await getProfile()
      setUser(response)
    } catch (error) {
      console.error('Error loading user:', error)
      localStorage.removeItem('token')
      setToken(null)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email, password) => {
    try {
      const response = await apiLogin(email, password)
      const { access_token, user } = response
      localStorage.setItem('token', access_token)
      setToken(access_token)
      setUser(user)
      toast.success('Connexion réussie !')
      return { success: true }
    } catch (error) {
      const message = error.response?.data?.error || 'Erreur de connexion'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const register = async (userData) => {
    try {
      const response = await apiRegister(userData)
      toast.success('Inscription réussie !')
      return { success: true, data: response }
    } catch (error) {
      const message = error.response?.data?.error || 'Erreur d\'inscription'
      toast.error(message)
      return { success: false, error: message }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    toast.success('Déconnexion réussie')
  }

  const value = {
    user,
    loading,
    token,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}