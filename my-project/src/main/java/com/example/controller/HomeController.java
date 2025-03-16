package com.example.demo;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class HomeController {

    // Главная страница
    @GetMapping("/")
    public String index() {
        return "index";
    }

    // Страница для пользователей
    @GetMapping("/user")
    public String userPage(Model model) {
        model.addAttribute("message", "Страница для пользователя");
        return "user";
    }

    // Страница для администраторов
    @GetMapping("/admin")
    public String adminPage(Model model) {
        model.addAttribute("message", "Страница для администратора");
        return "admin";
    }
}
