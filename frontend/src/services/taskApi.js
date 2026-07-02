import api from './api'

export const taskService = {
  // Récupérer toutes les tâches
  getAll: (params = {}) => {
    const query = new URLSearchParams(params).toString()
    return api.get(`/tasks${query ? '?' + query : ''}`)
      .then(res => res.data)
  },

  // Récupérer une tâche par ID
  getById: (id) => {
    return api.get(`/tasks/${id}`)
      .then(res => res.data)
  },

  // Créer une tâche
  create: (data) => {
    return api.post('/tasks', data)
      .then(res => res.data)
  },

  // Mettre à jour une tâche
  update: (id, data) => {
    return api.put(`/tasks/${id}`, data)
      .then(res => res.data)
  },

  // Mettre à jour le statut
  updateStatus: (id, status) => {
    return api.patch(`/tasks/${id}/status`, { status })
      .then(res => res.data)
  },

  // Supprimer une tâche
  delete: (id) => {
    return api.delete(`/tasks/${id}`)
      .then(res => res.data)
  }
}