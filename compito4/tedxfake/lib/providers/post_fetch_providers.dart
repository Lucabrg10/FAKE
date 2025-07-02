import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/post_fetch_service.dart';
import '../data/models/post.dart';

final postFetchServiceProvider = Provider<PostFetchService>((ref) {
  return PostFetchService(baseUrl: 'https://iqsdgjsd4f.execute-api.us-east-1.amazonaws.com/default/getPostsMongoDB');
});

final postsProvider = FutureProvider<List<Post>>((ref) async {
  final service = ref.read(postFetchServiceProvider);
  return service.fetchPosts();
});
