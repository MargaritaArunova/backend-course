package com.backend.course.controller;

import com.backend.course.model.Comment;
import com.backend.course.service.CommentService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/posts/{postId}/comments")
@RequiredArgsConstructor
public class CommentController {

    private final CommentService commentService;

    @GetMapping
    public List<Comment> getComments(@PathVariable Long postId) {
        return commentService.getCommentsForPost(postId);
    }

    @PostMapping
    public Comment addComment(@PathVariable Long postId,
                              @RequestParam("authorId") Long authorId,
                              @RequestParam("text") String text) {
        return commentService.addComment(postId, authorId, text);
    }

    @DeleteMapping("/{commentId}")
    public void deleteComment(@PathVariable Long postId,
                              @PathVariable Long commentId) {
        commentService.deleteComment(postId, commentId);
    }
}

