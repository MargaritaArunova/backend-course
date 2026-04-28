package com.backend.course.service;

import com.backend.course.exeption.NotFoundException;
import com.backend.course.model.Post;
import com.backend.course.model.User;
import com.backend.course.repository.CommentRepository;
import com.backend.course.repository.PostLikeRepository;
import com.backend.course.repository.PostRepository;
import com.backend.course.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@RequiredArgsConstructor
public class PostService {

    private final PostRepository postRepository;
    private final UserRepository userRepository;
    private final CommentRepository commentRepository;
    private final PostLikeRepository postLikeRepository;

    public List<Post> getAll() {
        return postRepository.findAll();
    }

    public Post createPost(Long authorId, String text) {
        User author = userRepository.findById(authorId)
                .orElseThrow(() -> new NotFoundException(User.class, authorId));

        Post post = new Post();
        post.setAuthorId(authorId);
        post.setText(text);

        return postRepository.save(post);
    }

    public Post getById(Long id) {
        return postRepository.findById(id)
                .orElseThrow(() -> new NotFoundException(Post.class, id));
    }

    @Transactional
    public void deletePost(Long id) {
        Post post = postRepository.findById(id)
                .orElseThrow(() -> new NotFoundException(Post.class, id));

        // Удаляем связанные данные: комментарии и лайки
        commentRepository.deleteByPostId(id);
        postLikeRepository.deleteByPostId(id);

        postRepository.delete(post);
    }
}

