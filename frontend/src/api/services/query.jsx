import apiIngestion from "../apiIngesion";
import api from "../api";

export const uploadFile = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiIngestion.post('/uploads', formData);
    return response.data;
}

export const mockUploadFiles = async (files) => {
    const formData = new FormData();
    files.forEach(file => {
        formData.append('files', file);
    });
    const response = await api.post('/api/user/uploads', formData);
    return response.data;
}