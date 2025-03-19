import { library, dom } from "@fortawesome/fontawesome-svg-core";
import {
  faCalendarAlt,
  faUsers,
  faGraduationCap,
  faHashtag,
  faBirthdayCake
} from "@fortawesome/free-solid-svg-icons";
import {
  faFacebookSquare,
  faInstagram,
  faTwitter,
  faGithub,
  faDiscord
} from "@fortawesome/free-brands-svg-icons";

library.add(
  faFacebookSquare,
  faInstagram,
  faTwitter,
  faGithub,
  faCalendarAlt,
  faUsers,
  faGraduationCap,
  faHashtag,
  faDiscord,
  faBirthdayCake
);

dom.i2svg();
