import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Box, List, ListItemButton, ListItemIcon, ListItemText, Typography, Divider } from '@mui/material';
import AccountCircleIcon from '@mui/icons-material/AccountCircle';
import BuildIcon from '@mui/icons-material/Build';
import PeopleIcon from '@mui/icons-material/People';

export default function MainLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  const [isAdmin, setIsAdmin] = useState(false);
  const [username, setUsername] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUsername(payload.username || '');
        setIsAdmin(payload.role?.includes('admin'));
      } catch {
        setUsername('');
        setIsAdmin(false);
      }
    }
  }, []);

  // Строим меню динамически
  const menu = [
    { text: 'Список оборудования', icon: <BuildIcon />, path: '/' },
    // Добавляем управление пользователями только для админа
    ...(isAdmin
      ? [{ text: 'Управление пользователями', icon: <PeopleIcon />, path: '/users' }]
      : [])
  ];

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Сайдбар */}
      <Box sx={{ width: 240, bgcolor: '#f5f5f5', p: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
          <AccountCircleIcon fontSize="large" />
          <Typography variant="subtitle1" sx={{ ml: 1 }}>
            {username}
          </Typography>
        </Box>
        <Divider />
        <List>
          {menu.map(item => (
            <ListItemButton
              key={item.text}
              selected={location.pathname === item.path}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          ))}
        </List>
      </Box>

      {/* Основной контент */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <Outlet />
      </Box>
    </Box>
  );
}
