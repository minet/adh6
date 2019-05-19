<template>
    <ul>
        <li v-for="r in results" v-bind:key="r.username">{{ r.firstName }} {{ r.lastName}} ({{ r.username}})</li>
    </ul>
</template>

<script>
    export default {
        name: "SearchResult",
        computed: {
            results() {
                return this.$store.state.memberSearch.result;
            }
        }
    }
</script>

<style scoped>

</style>