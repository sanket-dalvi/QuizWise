<script>
    document.addEventListener('DOMContentLoaded', function () {
        // Other code...

        function hideMessage() {
            document.querySelectorAll('.alert').forEach(function (alert) {
                alert.style.display = 'none';
            });
        }

        function showMessageForDuration(messageElement) {
            messageElement.style.display = 'block';
            setTimeout(function () {
                messageElement.style.display = 'none';
            }, 5000); // Hide the message after 5 seconds (5000 milliseconds)
        }

        // Initial options load
        document.querySelectorAll('.dynamic-fields label').forEach(function (label) {
            addDeleteButton(label);
        });

        // Show messages for a duration when the page loads
        document.querySelectorAll('.alert').forEach(function (messageElement) {
            showMessageForDuration(messageElement);
        });
    });
</script>
