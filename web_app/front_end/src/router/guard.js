import router from "./index";
import { getToken } from "@/utils/auth";

router.beforeEach((to, from, next)=>{
    const hasToken = getToken();
    if (hasToken) {
        if (to.path=="/login") {
            next("/");
        } else {
            next();
        }
    } else {
        if (to.path == "/login") {
            next();
        } else {
            next("/login");
        }
    }
})