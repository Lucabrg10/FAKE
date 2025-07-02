import 'package:http/http.dart' as http;
import 'dart:convert';
import '../data/models/post.dart';

class PostStorageService {
  final String baseUrl;

  PostStorageService({required this.baseUrl});

  Future<bool> savePost(Post post) async {
    try {
      final response = await http.post(
        Uri.parse(baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(post.toJson()),
      );

      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      print("Errore nel salvataggio post: $e");
      return false;
    }
  }
}
