<template>
    <div>
        <h1 class="title">Stock Dashboard </h1>
        <el-menu 
        :router="true"
        background-color="#001529"
        text-color="#fff">
            <menu-view v-for="(item, index) in menuData" :menu="item" :key="index"></menu-view>
        </el-menu>
    </div>
</template>

<script>
import { get } from '@/utils/http';
import MenuView from './MenuView.vue'

    export default {
        data() {
            return {
                menuData:[]
            }
        },
        created(){
            this.getMenu();
        },
        methods: {
            // get menu list
            async getMenu() {
                let {data} = await get("/menu");
                // console.log(data)
                this.menuData = data;
            }
        },
        components: {
            MenuView
        }
    }
</script>

<style lang="less" scoped>
.title {
    line-height: 50px;
    color: #fff;
    text-align: left;
    padding-left: 20px;
    font-size: 25px;
    margin-bottom: 0px;
    
}
</style>