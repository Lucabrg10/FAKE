class Post {
  final String title;
  final String text;
  final String author;
  final String imageUrl;
  final DateTime createdAt; // opzionale per ordinamento o salvataggio

  Post({
    required this.title,
    required this.text,
    required this.author,
    required this.imageUrl,
    required this.createdAt,
  });

  /// Factory per creare Post da JSON (es: da API)
  factory Post.fromJson(Map<String, dynamic> json) {
    return Post(
      title: json['title'] ?? '',
      text: json['text'] ?? '',
      author: json['author'] ?? '',
      imageUrl: json['image'] ?? '',
      createdAt: DateTime.tryParse(json['createdAt'] ?? '') ?? DateTime.now(),
    );
  }

  /// Converte Post in JSON (es: per salvataggio locale)
  Map<String, dynamic> toJson() => {
        'title': title,
        'text': text,
        'author': author,
        'image': imageUrl,
        'createdAt': createdAt.toIso8601String(),
      };
}
