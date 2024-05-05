<template>
    <div>
        <el-container>
            <el-aside width="220px" class="aside">
                <nav-left></nav-left>
            </el-aside>
            <el-container class="right-side">
                <el-header class="head">
                    <top-header></top-header>
                </el-header>
                <el-main class="main">
                    <keep-alive>
                        <router-view v-if="$route.meta.keepAlive"></router-view>
                    </keep-alive>
                    <router-view v-if="!$route.meta.keepAlive"></router-view>
                </el-main>
                <!-- <el-footer class="foot">
                        Copyright &copy; Binming
                </el-footer> -->
            </el-container>
        </el-container>
    </div>
</template>

<script>
import NavLeft from "@/components/NavLeft.vue";
import TopHeader from "@/components/TopHeader.vue";
    export default {
        components: {
            NavLeft,
            TopHeader
        }
    }
</script>

<style lang="less" scoped>
.head {
    background-color: #fff;
    line-height: 60px;
    box-shadow: 0 0px 1px rgba(0, 21, 41, 0.3);
}

.aside {
    height: 100vh;
    background: #001529;
}

.right-side {
    height: 100vh;
}

.main {
    background-color: #e9eef3;
}

.foot {
    text-align: center;
    color: #999;
    line-height: 60px;
    background-color: #e9eef3;
}
</style>
