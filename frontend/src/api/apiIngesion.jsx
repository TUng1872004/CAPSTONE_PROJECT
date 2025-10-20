import axios from "axios";
import { INGESTION_URL } from "@/constants/url";
import { useStore } from "@/stores/user";

const apiIngestion = axios.create({
    baseURL: INGESTION_URL,
});

apiIngestion.interceptors.request.use(
    (config) => {
        const token = useStore.getState().token;
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`; // later
        }
        else {
            delete config.headers['Authorization'];
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default apiIngestion;