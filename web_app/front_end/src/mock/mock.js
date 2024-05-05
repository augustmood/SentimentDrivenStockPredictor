import Mock from "mockjs";
// Network request delay simulation
Mock.setup({
    timeout: 500
})

// Login API
Mock.mock("http://localhost:8080/login", "post", (req)=>{
    const {username, password} = JSON.parse(req.body)
    if (username=="admin" && password==123456) {
        return {
            code: 200,
            success: true,
            message: "Login successfully.",
            token: "token",
            nickname: "admin"
        }
    } else {
        return {
            code: 100,
            success: false,
            message: "Incorrect username or password."
        }
    }
})

// User usage days API
Mock.mock("http://localhost:8080/in", "get", ()=>{
    return {
        code: 200,
        success: true,
        message: "request successfully",
        time: "2023-12-19"
    }
}
)

// Menu List
const menuList = [
    {
        name: "Home",
        icon: "el-icon-s-home",
        url: "/index",
    },
    {
        name: "Sentiment Impact",
        icon: "el-icon-s-flag",
        url: "/sentiment",
        children: [
            {
                name: "Community Impact",
                icon: "el-icon-s-comment",
                url: "/sentiment/community",
            },
            {
                name: "Media Impact",
                icon: "el-icon-s-platform",
                url: "/sentiment/media",
            },
        ]
    },
    {
        name: "Prediction",
        icon: "el-icon-s-marketing",
        url: "/prediction",
    },
]

Mock.mock("http://localhost:8080/menu","get",()=>{
    return{
        code:200,
        success:true,
        message:"Request successful",
        data:menuList
    }
})
