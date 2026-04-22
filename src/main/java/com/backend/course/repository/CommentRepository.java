package com.backend.course.repository;

import com.backend.course.model.Comment;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Repository
public class CommentRepository {

    private final Map<Long, Comment> storage = new ConcurrentHashMap<>();
    private final AtomicLong idGenerator = new AtomicLong(0);

    public Comment save(Comment comment) {
        if (comment.getId() == null) {
            comment.setId(idGenerator.incrementAndGet());
        }
        storage.put(comment.getId(), comment);
        return comment;
    }

    public Optional<Comment> findById(Long id) {
        return Optional.ofNullable(storage.get(id));
    }

    public List<Comment> findAll() {
        return new ArrayList<>(storage.values());
    }

    public void deleteById(Long id) {
        storage.remove(id);
    }

    public void delete(Comment comment) {
        storage.remove(comment.getId());
    }

    public boolean existsById(Long id) {
        return storage.containsKey(id);
    }

    public long count() {
        return storage.size();
    }

    public List<Comment> findByPostId(Long postId) {
        return storage.values().stream()
                .filter(comment -> comment.getPostId().equals(postId))
                .toList();
    }
}

