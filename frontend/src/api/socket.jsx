import { PRIMARY_URL } from '@/constants/url';
import { io } from "socket.io-client";
import toast from 'react-hot-toast';
const socket = io(PRIMARY_URL);

socket.on('connect', () => {
    toast.success('Connected to socket!');
});
 
export default socket;