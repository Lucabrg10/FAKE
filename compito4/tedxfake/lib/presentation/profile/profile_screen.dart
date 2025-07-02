import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/post.dart';
import '../../providers/post_fetch_providers.dart';
import '../../shared/widgets/post_card.dart';
import 'post_detail_screen.dart'; // o il percorso corretto

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final postsAsync = ref.watch(postsProvider);

    return Scaffold(
      appBar: AppBar(title: Text('Archivio Personale')),
      body: postsAsync.when(
        data: (posts) {
          if (posts.isEmpty) {
            return Center(child: Text('Nessun post salvato'));
          }
          return GridView.builder(
            padding: EdgeInsets.all(12),
            gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,  // 2 colonne
              crossAxisSpacing: 10,
              mainAxisSpacing: 10,
              childAspectRatio: 0.75,
            ),
            itemCount: posts.length,
            itemBuilder: (context, index) {
              final post = posts[index];
              return PostCard(post: post, compact: true);
            },
          );
        },
        loading: () => Center(child: CircularProgressIndicator()),
        error: (err, _) => Center(child: Text('Errore: $err')),
      ),
    );
  }
}
