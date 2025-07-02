import 'package:http/http.dart' as http;
import 'dart:convert';
import '../data/models/post.dart';

class PostFetchService {
  final String baseUrl;

  PostFetchService({required this.baseUrl});

  Future<List<Post>> fetchPosts() async {
    final response = await http.get(Uri.parse(baseUrl));

    if (response.statusCode == 200) {
      final List<dynamic> jsonList = jsonDecode(response.body);
      return jsonList.map((json) => Post.fromJsonDB(json)).toList();
    } else {
      throw Exception('Errore nel recupero dei post');
    }
  }
}
