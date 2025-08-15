// src/pages/MainPage.js
import React from "react";
import { Container, Row, Col, Card, Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import "../styles/mainpage.css";

const MainPage = () => {
  const navigate = useNavigate();

  return (
    <div className="main-page">
      {/* Hero Section */}
      <section className="hero text-center text-white">
        <div className="overlay"></div>
        <Container className="hero-content">
          <h1 className="display-4 fw-bold">Connect Smarter. Chat Better.</h1>
          <p className="lead">
            A modern, secure, and beautifully designed platform for all your conversations.
          </p>
          <Button
            variant="primary"
            size="lg"
            className="shadow-lg"
            onClick={() => navigate("/chat/new")}
          >
            Start Chatting
          </Button>
        </Container>
      </section>

      {/* Features Section */}
      <section className="py-5 bg-light">
        <Container>
          <Row className="text-center mb-4">
            <h2 className="fw-bold">Why Choose Our Platform?</h2>
            <p className="text-muted">
              Streamlined chat management, intuitive UI, and blazing speed.
            </p>
          </Row>
          <Row className="g-4 align-items-stretch">
            <Col md={4}>
              <Card className="feature-card shadow-sm border-0 h-100">
                <Card.Body className="d-flex flex-column align-items-center text-center">
                  <div className="icon-circle bg-primary text-white">
                    <i className="bi bi-speedometer2"></i>
                  </div>
                  <h5 className="mt-3">Fast & Secure</h5>
                  <p className="text-muted">
                    Experience real-time messaging with enterprise-grade security.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="feature-card shadow-sm border-0 h-100">
                <Card.Body className="d-flex flex-column align-items-center text-center">
                  <div className="icon-circle bg-success text-white">
                    <i className="bi bi-chat-dots"></i>
                  </div>
                  <h5 className="mt-3">Organized Chats</h5>
                  <p className="text-muted">
                    Categorize and filter conversations effortlessly.
                  </p>
                </Card.Body>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="feature-card shadow-sm border-0 h-100">
                <Card.Body className="d-flex flex-column align-items-center text-center">
                  <div className="icon-circle bg-warning text-white">
                    <i className="bi bi-graph-up"></i>
                  </div>
                  <h5 className="mt-3">Analytics</h5>
                  <p className="text-muted">
                    Get insights on chat activity and engagement trends.
                  </p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Testimonials Section */}
      <section className="py-5">
        <Container>
          <Row className="text-center mb-4">
            <h2 className="fw-bold">What Our Users Say</h2>
          </Row>
          <Row className="g-4">
            <Col md={4}>
              <Card className="testimonial-card border-0 shadow-sm p-4 h-100">
                <p>"Absolutely love the simplicity and speed. Best chat app I’ve used!"</p>
                <h6 className="fw-bold mt-auto">– Sarah L.</h6>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="testimonial-card border-0 shadow-sm p-4 h-100">
                <p>"The clean design makes it easy to focus on conversations that matter."</p>
                <h6 className="fw-bold mt-auto">– James R.</h6>
              </Card>
            </Col>
            <Col md={4}>
              <Card className="testimonial-card border-0 shadow-sm p-4 h-100">
                <p>"I can finally manage all my chats in one place without the clutter."</p>
                <h6 className="fw-bold mt-auto">– Priya K.</h6>
              </Card>
            </Col>
          </Row>
        </Container>
      </section>

      {/* Call To Action */}
      {/* <section className="cta-section text-center text-white py-5">
        <div className="overlay"></div>
        <Container>
          <h2 className="fw-bold mb-3">Ready to start your first conversation?</h2>
          <Button
            variant="light"
            size="lg"
            onClick={() => navigate("/register")}
          >
            Create Your Free Account
          </Button>
        </Container>
      </section> */}
    </div>
  );
};

export default MainPage;
