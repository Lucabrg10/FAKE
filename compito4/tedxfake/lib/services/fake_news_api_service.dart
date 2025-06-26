// lib/services/fake_news_api_service.dart
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../data/models/post.dart';

class FakeNewsApiService {
  Future<Post> generateFakePost(String prompt) async {
    final response = await http.post(
      Uri.parse('https://api.example.com/generate'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'prompt': prompt}),
    );

    if (response.statusCode == 200) {
      return Post.fromJson(jsonDecode(response.body));
    } else {
      throw Exception("Errore nella generazione");
    }
  }
}
