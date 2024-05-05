<template>
    <div>
        <el-submenu v-if="menu.children" :index="menu.url" class="menu-item">
            <template slot="title">
                <i :class="menu.icon"></i>
                <span slot="title"> {{ menu.name }}</span>
            </template>
            <menu-view v-for="(item, index) in menu.children" :key="index" :menu="item"></menu-view>
        </el-submenu>

        <el-menu-item v-else :index="menu.url" class="menu-item">
            <i :class="menu.icon"></i>
            <span slot="title">{{ menu.name }}</span>
        </el-menu-item>
    </div>
</template>

<script>
    export default {
        name: "MenuView", // need name when component invoking itself
        props: {
            menu: {
                type: Object,
                required: true
            }
        }
    }
</script>

<style lang="less" scoped>
.menu-item {
    width: 220px;
}
</style>