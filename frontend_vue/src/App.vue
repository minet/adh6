<template>
    <div id="app">
        <navigation-bar></navigation-bar>
        <div class="container-fluid">
            <div class="row">
                <router-view/>
            </div>
        </div>
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

