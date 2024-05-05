<template>
    <div>
        <div class="fr">
            <el-dropdown @command="handleCommand">
                <span class="el-dropdown-link" style="cursor: pointer;" @mouseover="hovering = true" @mouseleave="hovering = false">
                    {{ info }}<i class="el-icon-arrow-down el-icon--right"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                    <el-dropdown-item command="profile">Profile</el-dropdown-item>
                    <el-dropdown-item command="settings">Settings</el-dropdown-item>
                    <el-dropdown-item command="logout">Logout</el-dropdown-item>
                </el-dropdown-menu>
            </el-dropdown>
        </div>
        <div class="clear"></div>
    </div>
</template>

<script>
import {get} from "@/utils/http"
import { removeToken } from '@/utils/auth';
    export default {
        data() {
            return {
                info: sessionStorage.getItem("nickname"),
                hovering: false
            }
        },
        created() {
            // Get the duration of use
            this.usageDuration();
        },
        methods: {
            handleCommand(item){
                if (item == "logout") {
                    removeToken();
                    this.$router.push("/login");
                }
            },
            usageDuration(){
                get("/in").then((res)=>{
                    this.time = res.time 
                })
            }
        },
        computed: {
            // days() {
            //     let now = new Date();
            //     let target = this.time? new Date(this.time): new Date();
            //     return Math.floor((now - target) / 1000 / 60 / 60 / 24)
            // }
        }
    }
</script>

<style lang="less" scoped>
.date {
    margin-right: 50px;
    .tips {
        font-size: 24px;
        color: #5696ff;
    }
}

</style>