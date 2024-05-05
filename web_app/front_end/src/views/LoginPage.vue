<template>
    <div class="login-container">
        <el-row type="flex" justify="center">
            <el-card class="box-card">
                <div slot="header" class="clearfix">
                    <h2>Stock Price Prediction Dashboard</h2>
                </div>
                <div>
                    <el-form
                    :model="ruleForm" 
                    :rules="rules" 
                    ref="ruleForm" 
                    label-width="80px" 
                    class="demo-ruleForm">
                        <el-form-item label="Username:" prop="username">
                            <el-input v-model="ruleForm.username"></el-input>
                        </el-form-item>
                        <el-form-item label="Password:" prop="password">
                            <el-input type="password" v-model="ruleForm.password"></el-input>
                        </el-form-item>
                        <el-form-item>
                            <el-button 
                            type="primary" 
                            style="width: 100%" 
                            @click="login"
                            :loading="loading"> Login </el-button>
                        </el-form-item>
                    </el-form>
                </div>
            </el-card>
        </el-row>
    </div>
</template>

<script>
import {post} from "@/utils/http"
import {setToken} from "@/utils/auth"
    export default {
        data(){
            return {
                loading: false,
                ruleForm: {
                    // Replace 'admin' and '123456' with your desired default values
                    username: 'admin', 
                    password: '123456',
                },
                rules: {
                    username:[
                    {required: true, message: "Username is required", trigger: 'blur'},
                    {pattern: /^\w{4,8}$/, message: "Username: 4-8 characters, letters and numbers only.", trigger: 'blur'},
                    ],
                    password:[
                    {required: true, message: "Password is required", trigger: 'blur'},
                    {pattern: /^\d{6}$/, message: "Password: 6 characters, numbers only.", trigger: 'blur'},
                    ],
                }
            }
        },
        methods: {
            login(){
                this.$refs.ruleForm.validate((valid)=>{
                    if (valid) {
                        this.loading = true;
                        post("/login", this.ruleForm).then(res=>{
                            this.loading=false;
                            setToken(res.token);
                            sessionStorage.setItem('nickname', res.nickname)
                            this.$router.push("/")
                        }).catch((error)=>{
                            this.loading=false;
                            console.log(error);
                        })
                    }
                })
            }
        }
    }
</script>

<style lang="less" scoped>
@bgColor: #5696ff;
@width: 500px;
.login-container {
    display: flex; 
    height: 100vh; 
    align-items: center; 
    justify-content: center;
}
.box-card {
    width: @width;
    // margin-top: (@width / 2);
    h2 {
        text-align: center
    }
}
</style>