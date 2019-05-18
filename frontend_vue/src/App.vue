<template>
    <div id="app">
        <navigation-bar></navigation-bar>
        <router-view/>
    </div>
</template>

<script>

    import NavigationBar from './components/NavigationBar/NavigationBar'

    export default {
        components: {
            NavigationBar,
        }
    }
</script>

<style>
</style>

