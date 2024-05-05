export function setToken(token) {
    sessionStorage.setItem("token", token);
}

export function getToken(){
    return sessionStorage.getItem("token");
}

export function removeToken(){
    sessionStorage.clear();
}