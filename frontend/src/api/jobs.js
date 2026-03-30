import api from './index'

export const getJobs = (params) => api.get('/jobs', { params })
export const exportJobs = (params) => api.get('/jobs/export', { params, responseType: 'blob' })
