document.querySelector('.search-icon').addEventListener('click', function () {
    document.getElementById('search-form').submit();
});

document.getElementById('searchInput').addEventListener('input', function () {
    var searchValue = this.value.toLowerCase();
    var books = document.getElementsByClassName('book-card');
    var bookList = document.getElementById('bookList');

    for (var i = 0; i < books.length; i++) {
        var title = books[i].getElementsByClassName('book-title')[0].innerText.toLowerCase();
        var author = books[i].getElementsByClassName('book-author')[0].innerText.toLowerCase();

        if (title.includes(searchValue) || author.includes(searchValue)) {
            books[i].style.display = '';
        } else {
            books[i].style.display = 'none';
        }
    }

    // Remove filtered-out items and move remaining items to the top
    var removedItems = document.querySelectorAll('.book-card:not([style="display: ;"])');
    removedItems.forEach(function (item) {
        bookList.removeChild(item.parentElement.parentElement);
    });
});
