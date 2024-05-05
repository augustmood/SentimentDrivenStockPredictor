import axios from "axios";
import { Message } from 'element-ui';
import {getToken} from './auth'
const service = axios.create({
    baseURL: "http://localhost:8080/",
    timeout: 5000
})

// Request Interceptor
service.interceptors.request.use((config)=>{
    if (getToken()) {
        config.headers.token=getToken()
    }
    return config
}), ()=>{
    Message({
        type: "error",
        message: "Request Error"
    })
    return Promise.reject(new Error("Request Error"))
}

export default service

// Response Interceptor
service.interceptors.response.use((res)=> {
    const result = res.data; 
    if (result.success) {
        return result;
    } else {
        Message({
            type: "error",
            message: result.message || "Request Error"
        })
        return Promise.reject(new Error(result.message || "Request Error"))
    }

}), ()=>{
    Message({
        type: "error",
        message: "Request Error"
    })
    return Promise.reject(new Error("Request Error"))
}
