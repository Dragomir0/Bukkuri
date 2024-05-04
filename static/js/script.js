document.querySelector('.search-icon').addEventListener('click', function () {
    document.getElementById('search-form').submit();
});

document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');

    searchInput.addEventListener('input', function() {
        const searchValue = this.value.toLowerCase();
        const books = document.querySelectorAll('.book-disponibles');

        books.forEach(book => {
            const title = book.querySelector('.book-title').innerText.toLowerCase();
            const author = book.querySelector('.book-author').innerText.toLowerCase();

            if (title.includes(searchValue) || author.includes(searchValue)) {
                book.style.display = '';  // Show the book
            } else {
                book.style.display = 'none';  // Hide the book
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const searchBookCards = document.querySelectorAll('.search-book-card');
    searchBookCards.forEach(card => {
        card.addEventListener('click', function() {
            this.classList.toggle('selected');
            const bookId = this.getAttribute('data-book-id');
            const input = document.querySelector(`input[name="book_ids"][value="${bookId}"]`);
            input.checked = !input.checked;  
        });
    });
});

