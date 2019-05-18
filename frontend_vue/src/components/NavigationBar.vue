<template>
    <nav class="navbar navbar-expand-lg navbar-dark minet-bg-blue">
        <a class="navbar-brand" href="#">
            <img src="../assets/logo.png" height="30" class="d-inline-block align-top" alt="">
            ADH6
        </a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <ul class="navbar-nav mr-auto">
                <navigation-bar-link content="Home" route="home"></navigation-bar-link>
                <navigation-bar-link content="Adhérent" route="member-search"></navigation-bar-link>
            </ul>
            <form class="form-inline my-2 my-lg-0">
                <input class="form-control mr-sm-2" type="search" placeholder="Search" aria-label="Search">
                <button class="btn btn-outline-info my-2 my-sm-0" type="submit">Search</button>
            </form>
        </div>
    </nav>
</template>

<script>
    import NavigationBarLink from './NavigationBarLink'

    export default {
        components: {
            NavigationBarLink,
        }
    }
</script>

<style>
    .minet-bg-blue {
        background-color: #0056b3;
    }
</style>

