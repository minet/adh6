# Combobox partagée

`ComboboxComponent` est un composant standalone sans dépendance aux API métier.
Il propose un champ éditable avec des suggestions filtrées pendant la saisie.
Les flèches naviguent entre les suggestions, Entrée sélectionne et Échap ferme la liste.
Une saisie correspondant exactement à un libellé unique sélectionne également l'option.
Une saisie inconnue reste visible mais invalide : aucune valeur libre n'est acceptée.

Importer `ComboboxComponent` et `ReactiveFormsModule` dans le composant consommateur :

```ts
options: ComboboxOption[] = [
  {value: 1, label: "Option A"},
  {value: 2, label: "Option B"},
];
form = new FormGroup({choice: new FormControl<number | null>(null, Validators.required)});
```

```html
<form [formGroup]="form">
  <app-combobox
    formControlName="choice"
    [options]="options"
    label="Choix"
    placeholder="Choisir une option" />
</form>
```

Les valeurs des options sont des nombres ou des chaînes ; leur type est conservé.
`null` représente l'absence de sélection. Ajouter `Validators.required` au contrôle
parent pour rendre le choix obligatoire.

`loading` et `unavailable` désactivent la liste et rendent le contrôle parent invalide.
Toute valeur absente des options est également invalide, même affectée par code.
`inputId` permet d'associer un `<label for="…">` externe au champ.

Les barres de recherche générales utilisent des champs texte natifs, sans combobox
ni requêtes de suggestions. Les combobox restent réservées aux filtres et formulaires.

Le composant propose également `mode="search"` : le contrôle émet le texte
saisi, sans obliger à sélectionner une suggestion. Le choix d'une suggestion émet
sa valeur et l'événement `optionSelected`. Le texte reste éditable pendant le
chargement ; en cas d'erreur, seule l'aide par suggestions est indisponible.
`[filterLocally]="false"` permet d'afficher les suggestions déjà filtrées par le
serveur, notamment lors d'une recherche par mail.

`[showSuggestions]="false"` masque les suggestions et leur bouton, tout en gardant
la saisie et l'intégration au formulaire.

`MemberSuggestionsService` ne cherche qu'à partir de deux caractères et ne charge
les noms que si le nombre total de résultats respecte le seuil de confidentialité
de la liste. Le consommateur temporise la saisie et annule les requêtes précédentes.

`RoomSelectComponent` est l'adaptateur métier : il charge toutes les pages de chambres,
trie leurs numéros et utilise la combobox partagée. `valueField="id"` retourne
l'identifiant en base au lieu du numéro affiché.

Les tests s'exécutent depuis `frontend` avec `npm test`.
