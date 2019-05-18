<template>
    <nav class="navbar navbar-expand-lg navbar-dark minet-bg-blue">
        <router-link v-bind:to="{name:'home'}" class="navbar-brand" href="#">
            <img src="../../assets/logo.png" height="30" class="d-inline-block align-top" alt="">
            ADH6
        </router-link>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent"
                aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span class="navbar-toggler-icon"></span>
        </button>

        <div class="collapse navbar-collapse" id="navbarSupportedContent">
            <input class="form-control mr-sm-2 w-100" type="search" placeholder="Search" aria-label="Search">
            <ul class="navbar-nav mr-auto">
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button"
                       data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                        Plus
                    </a>
                    <div class="dropdown-menu dropdown-menu-right" aria-labelledby="navbarDropdown">
                        <router-link v-bind:to="{name:'member-search'}" nameclass="dropdown-item" href="#">
                            <a class="dropdown-item" href="#">
                                Adhérent
                            </a>
                        </router-link>
                        <a class="dropdown-item" href="#">Appareil</a>
                        <a class="dropdown-item" href="#">Chambre</a>
                        <a class="dropdown-item" href="#">Switch</a>
                        <div class="dropdown-divider"></div>
                        <a class="dropdown-item" href="#">Déconnexion</a>
                    </div>
                </li>
            </ul>
        </div>
    </nav>
</template>

<script>

    export default {}
</script>

<style>
    .minet-bg-blue {
        background-color: #0056b3;
    }
</style>

