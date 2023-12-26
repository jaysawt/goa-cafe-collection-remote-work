function search() {
    var input = document.getElementById('searchInput');
    var searchInput = input.value.toLowerCase();
    var allCafes = document.querySelectorAll('.all_cafes');
    var notFoundMessage = document.getElementById('not_found');
    var foundCafes = false;

    allCafes.forEach(function (cafe) {
        var cafeName = cafe.querySelector('.card-title').textContent.toLowerCase();
        var displayStyle = cafeName.includes(searchInput) ? 'block' : 'none';
        cafe.style.display = displayStyle;
        foundCafes = foundCafes || displayStyle === 'block';   /*if one card is found then foundCafes is set to true and remains true it only becomes false when no cafe card is found.*/
    });

    // Show or hide the "No cafes found" message based on the flag
    notFoundMessage.style.display = foundCafes ? 'none' : 'block';
}
