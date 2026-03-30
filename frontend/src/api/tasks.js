import api from './index'

export const getTasks = (params) => api.get('/tasks', { params })
export const createTask = (data) => api.post('/tasks', data)
export const stopTask = (id) => api.post(`/tasks/${id}/stop`)
export const getTaskLogs = (id) => api.get(`/tasks/${id}/logs`)
