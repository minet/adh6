<template>
    <li class="nav-item" v-bind:class="{ active: isActive }">
        <router-link class="nav-link" v-bind:to="{name:this.route}">{{ this.content }}</router-link>
    </li>
</template>

<script>
    export default {
        name: 'NavigationBarLink',
        props: ['content', 'route'],
        computed: {
            isActive() {
                return this.route === this.$route.name;
            }
        }
    }
</script>

<style scoped>

</style>