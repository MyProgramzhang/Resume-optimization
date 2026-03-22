export type LinkItem = {
  label: string;
  url: string;
};

export type Basics = {
  name: string;
  phone: string;
  email: string;
  location: string;
  links: LinkItem[];
};

export type ExperienceItem = {
  block_id: string;
  company: string;
  title: string;
  start_date: string;
  end_date: string;
  bullets: string[];
};

export type EducationItem = {
  block_id: string;
  school: string;
  degree: string;
  major: string;
  start_date: string;
  end_date: string;
};

export type ProjectItem = {
  block_id: string;
  name: string;
  role: string;
  start_date: string;
  end_date: string;
  bullets: string[];
};

export type SkillGroup = {
  category: string;
  items: string[];
};

export type ResumeSchema = {
  basics: Basics;
  summary: string;
  experience: ExperienceItem[];
  education: EducationItem[];
  projects: ProjectItem[];
  skills: SkillGroup[];
};
