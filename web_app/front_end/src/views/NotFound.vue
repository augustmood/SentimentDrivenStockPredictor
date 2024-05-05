<template>
    <div class="not-found">
        <el-empty description="Under Construction">
            <el-button type="primary" @click="$router.push('/')">Back</el-button>
        </el-empty>
    </div>
</template>

<script>
    export default {
    }
</script>

<style lang="less" scoped>
.not-found {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}
</style>